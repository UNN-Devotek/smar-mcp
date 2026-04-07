import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { SmartsheetAPI } from "../apis/smartsheet-api.js";
import { z } from "zod";
import { limitResponseSize } from "../utils/response-limiter.js";

const summaryFieldSchema = z.object({
  id: z.number().optional().describe("Field ID (required for updates)"),
  title: z.string().describe("Field title/name"),
  type: z.enum(["TEXT_NUMBER", "DATE", "CHECKBOX", "CONTACT_LIST", "PICKLIST"])
    .describe("Field type"),
  formula: z.string().optional().describe(
    "Formula for the field. Use [Column Name]:[Column Name] syntax for whole-column ranges — these cover all rows including future additions. " +
    "COUNTIF/COUNTIFS with ISDATE(@cell) works for date columns. " +
    "Percent fields should return a decimal (0–1); pair with numberFormat=3 format string."
  ),
  value: z.any().optional().describe("Static value (used when no formula)"),
  format: z.string().optional().describe(
    "17-element comma-separated format string controlling display. Key positions: " +
    "[11]=currency(13=USD $), [12]=decimalCount(0-5), [13]=thousandsSeparator(1=yes), " +
    "[14]=numberFormat(1=NUMBER, 2=CURRENCY, 3=PERCENT). " +
    "Examples: currency no-decimal=',,,,,,,,,,,,13,0,1,2,,', integer=',,,,,,,,,,,,0,1,1,,', percent=',,,,,,,,,,,,0,,3,,'"
  ),
});

export function getSummaryTools(server: McpServer, api: SmartsheetAPI, allowDeleteTools: boolean) {

  server.tool(
    "get_sheet_summary",
    "Retrieves the sheet summary, including all summary fields and their current values",
    {
      sheetId: z.string().describe("The ID of the sheet"),
      include: z.string().optional().describe("Comma-separated elements to include (e.g. 'writerInfo')"),
    },
    async ({ sheetId, include }) => {
      try {
        console.error(`Getting summary for sheet ${sheetId}`);
        const result = await api.summary.getSummary(sheetId, include);
        return limitResponseSize(result);
      } catch (error: any) {
        console.error(`Failed to get summary for sheet ${sheetId}`, { error });
        return {
          content: [{ type: "text", text: `Failed to get sheet summary: ${error.message}` }],
          isError: true,
        };
      }
    }
  );

  server.tool(
    "get_sheet_summary_fields",
    "Retrieves all summary fields defined on a sheet",
    {
      sheetId: z.string().describe("The ID of the sheet"),
      include: z.string().optional().describe("Comma-separated elements to include (e.g. 'writerInfo')"),
    },
    async ({ sheetId, include }) => {
      try {
        console.error(`Getting summary fields for sheet ${sheetId}`);
        const result = await api.summary.getSummaryFields(sheetId, include);
        return limitResponseSize(result);
      } catch (error: any) {
        console.error(`Failed to get summary fields for sheet ${sheetId}`, { error });
        return {
          content: [{ type: "text", text: `Failed to get sheet summary fields: ${error.message}` }],
          isError: true,
        };
      }
    }
  );

  server.tool(
    "add_sheet_summary_fields",
    "Adds one or more new summary fields to a sheet. Each field can have a formula or a static value.",
    {
      sheetId: z.string().describe("The ID of the sheet"),
      fields: z.array(summaryFieldSchema.omit({ id: true }))
        .describe("Array of summary fields to add"),
    },
    async ({ sheetId, fields }) => {
      try {
        console.error(`Adding ${fields.length} summary field(s) to sheet ${sheetId}`);
        const result = await api.summary.addSummaryFields(sheetId, fields);
        return {
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        };
      } catch (error: any) {
        console.error(`Failed to add summary fields to sheet ${sheetId}`, { error });
        return {
          content: [{ type: "text", text: `Failed to add sheet summary fields: ${error.message}` }],
          isError: true,
        };
      }
    }
  );

  server.tool(
    "update_sheet_summary_fields",
    "Updates one or more existing summary fields on a sheet. Each field must include its ID.",
    {
      sheetId: z.string().describe("The ID of the sheet"),
      fields: z.array(summaryFieldSchema)
        .describe("Array of summary fields to update. Each must include the field 'id'."),
    },
    async ({ sheetId, fields }) => {
      try {
        console.error(`Updating ${fields.length} summary field(s) on sheet ${sheetId}`);
        const result = await api.summary.updateSummaryFields(sheetId, fields);
        return {
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        };
      } catch (error: any) {
        console.error(`Failed to update summary fields on sheet ${sheetId}`, { error });
        return {
          content: [{ type: "text", text: `Failed to update sheet summary fields: ${error.message}` }],
          isError: true,
        };
      }
    }
  );

  if (allowDeleteTools) {
    server.tool(
      "delete_sheet_summary_fields",
      "Deletes one or more summary fields from a sheet by their field IDs",
      {
        sheetId: z.string().describe("The ID of the sheet"),
        fieldIds: z.array(z.number()).describe("Array of summary field IDs to delete"),
      },
      async ({ sheetId, fieldIds }) => {
        try {
          console.error(`Deleting ${fieldIds.length} summary field(s) from sheet ${sheetId}`);
          const result = await api.summary.deleteSummaryFields(sheetId, fieldIds);
          return {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          };
        } catch (error: any) {
          console.error(`Failed to delete summary fields from sheet ${sheetId}`, { error });
          return {
            content: [{ type: "text", text: `Failed to delete sheet summary fields: ${error.message}` }],
            isError: true,
          };
        }
      }
    );
  }
}
