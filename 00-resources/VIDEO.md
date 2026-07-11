#AWS #MCP #ModelContextProtocol #Cognito #OAuth #AWSLambda #APIGateway #Terraform #Python #ClaudeAI #Serverless

*Secure a Remote MCP Server with Amazon Cognito (OAuth 2.0)*

How do you let Claude call your AWS tools securely — with a real login, no local proxy, and no API keys to hand around?

In this project we connect Claude directly to a remote MCP server on AWS, secured with Amazon Cognito. You paste one URL into Claude, sign in through a real Cognito login page in your browser, and Claude can query your live AWS costs. No proxy script running on your machine, no SigV4 signing, nothing installed locally.

Last time we bridged Claude to AWS with a local stdio proxy that signed every request with SigV4. This time the proxy is gone. The connector speaks OAuth, and an API Gateway Lambda plays the role of the OAuth authorization server — brokering Claude's login against Cognito and validating the access token on every tool call.

We use AWS Cost Explorer as the example tool set — six cost-query tools behind one router Lambda — but the auth pattern works for any Lambda-backed MCP server.

WHAT YOU'LL LEARN
• Remote MCP over OAuth — connect claude.ai to AWS with just a URL, no local proxy or SigV4
• Turning an API Gateway Lambda into an OAuth authorization server (RFC 8414 metadata + RFC 7591 dynamic client registration)
• Brokering claude.ai's dynamic redirect URI against Cognito's exact-match callback
• Validating Cognito access tokens inside the Lambda via the /oauth2/userInfo endpoint
• Least-privilege fan-out — a router Lambda that invokes six scoped Cost Explorer tools
• Authentication vs authorization — why every authenticated user is authorized here, and when that is fine

INFRASTRUCTURE DEPLOYED
• API Gateway HTTP API — public routes; authentication enforced inside the Lambda (OAuth endpoints + /mcp)
• MCP router Lambda (Python 3.14) — serves the OAuth flow and the MCP JSON-RPC endpoint, invokes the cost tools
• 6 Cost Explorer Lambdas — each with its own scoped execution role
• Amazon Cognito user pool + Hosted UI + confidential MCP OAuth client
• DynamoDB table — transient OAuth state, 5-minute TTL
• All provisioned with Terraform in a single apply, torn down with a single command

GitHub
https://github.com/mamonaco1973/aws-cognito-mcp

README
https://github.com/mamonaco1973/aws-cognito-mcp/blob/main/README.md

TIMESTAMPS
00:00 Live Demo
00:41 Architecture
01:35 Securing MCP
02:17 Deploy It Yourself
