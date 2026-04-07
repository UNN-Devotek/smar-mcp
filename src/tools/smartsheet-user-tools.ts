import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { SmartsheetAPI } from "../apis/smartsheet-api.js";
import { z } from "zod";
import { limitResponseSize } from "../utils/response-limiter.js";

export function getUserTools(server: McpServer, api: SmartsheetAPI) {

    // Tool: Get Current User
    server.tool(
        "get_current_user",
        "Gets the current user's information",
        async () => {
        try {
            console.error("Getting current user");
            const user = await api.users.getCurrentUser();
            
            return limitResponseSize(user);
        } catch (error: any) {
            console.error("Failed to get current user", { error });
            return {
            content: [
                {
                type: "text",
                text: `Failed to get current user: ${error.message}`
                }
            ],
            isError: true
            };
        }
        }
    );

    // Tool: Get User
    server.tool(
        "get_user",
        "Gets a user's information by ID",
        {
        userId: z.string().describe("ID of the user to get")
        },
        async ({ userId }) => {
        try {
            console.error(`Getting user with ID: ${userId}`);
            const user = await api.users.getUserById(userId);
            
            return limitResponseSize(user);
        } catch (error: any) {
            console.error("Failed to get user", { error });
            return {
            content: [
                {
                type: "text",
                text: `Failed to get user: ${error.message}`
                }
            ],
            isError: true
            };
        }
        }
    );

    server.tool(
        "list_users",
        "Lists all users",
        async () => {
            try {
                console.error("Listing all users");
                const users = await api.users.listUsers();
                
                return limitResponseSize(users);
            } catch (error: any) {
                console.error("Failed to list users", { error });
                return {
                    content: [
                        {
                            type: "text",
                            text: `Failed to list users: ${error.message}`
                        }
                    ],
                    isError: true
                };
            }
        }
    );

}
