import { SmartsheetAPI } from "./smartsheet-api.js";

export class SmartsheetSummaryAPI {
  private api: SmartsheetAPI;

  constructor(api: SmartsheetAPI) {
    this.api = api;
  }

  async getSummary(sheetId: string, include?: string): Promise<any> {
    return this.api.request('GET', `/sheets/${sheetId}/summary`, undefined, { include });
  }

  async getSummaryFields(sheetId: string, include?: string): Promise<any> {
    return this.api.request('GET', `/sheets/${sheetId}/summary/fields`, undefined, { include });
  }

  async addSummaryFields(sheetId: string, fields: any[]): Promise<any> {
    return this.api.request('POST', `/sheets/${sheetId}/summary/fields`, fields);
  }

  async updateSummaryFields(sheetId: string, fields: any[]): Promise<any> {
    return this.api.request('PUT', `/sheets/${sheetId}/summary/fields`, fields);
  }

  async deleteSummaryFields(sheetId: string, fieldIds: number[]): Promise<any> {
    return this.api.request('DELETE', `/sheets/${sheetId}/summary/fields`, undefined, {
      ids: fieldIds.join(',')
    });
  }
}
