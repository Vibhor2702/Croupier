# Architecture Diagram Guide

## What to Create

Create a **high-level architecture diagram** showing the Croupier system structure.

## Diagram Components

### 1. Layered Architecture
Show these layers vertically:
- **Client Layer** (Top)
- **API Layer (FastAPI Routers)**
- **Service Layer (Business Logic)**
- **Repository Layer (Data Access)**
- **Database Layer (MongoDB)** (Bottom)

### 2. Multi-Tenancy Structure
Show:
- Master Database (organizations, admin_users collections)
- Dynamic Collections (org_acme, org_demo, etc.)
- How they relate

### 3. Request Flow
Show arrows indicating:
- POST /org/create → Service → Repository → DB
- JWT authentication flow
- Dynamic collection creation

## Recommended: Use draw.io

### Step-by-Step with draw.io:

1. **Open:** https://app.diagrams.net/
2. **Choose:** "Blank Diagram" → Save to "Device"
3. **Create Layers:**
   - Add 5 rectangles stacked vertically
   - Label: Client, API, Service, Repository, Database
   - Style: Use different colors per layer

4. **Add Details:**
   - In API layer: Add text "Routers: /org/create, /org/get, etc."
   - In Service: "OrganizationService, AuthService"
   - In Repository: "OrganizationRepo, AdminRepo"
   - In Database: "Master DB + org_<name> collections"

5. **Add Arrows:**
   - Connect layers with arrows (top to bottom)
   - Add labels on arrows: "HTTP", "Business Logic", "Data Access"

6. **Add JWT Flow (Side):**
   - Small box: "POST /admin/login"
   - Arrow to "JWT Token"
   - Show token used in authenticated requests

7. **Export:**
   - File → Export as → PNG
   - Name: `Croupier_Architecture_Diagram.png`
   - High quality (300 DPI)

8. **Save to repo:**
   - Place in root: `Croupier_Architecture_Diagram.png`

## Alternative: Mermaid in README

Add this to your README.md (GitHub renders it automatically):

```markdown
## Architecture Diagram

```mermaid
graph TB
    subgraph Client Layer
        A[Web/Mobile Apps]
    end
    
    subgraph API Layer
        B[FastAPI Routers]
        B1[/org/create]
        B2[/org/get]
        B3[/org/update]
        B4[/org/delete]
        B5[/admin/login]
    end
    
    subgraph Service Layer
        C[OrganizationService]
        D[AuthService]
    end
    
    subgraph Repository Layer
        E[OrganizationRepository]
        F[AdminRepository]
    end
    
    subgraph Database Layer
        G[MongoDB Master DB]
        G1[organizations collection]
        G2[admin_users collection]
        H[Dynamic Collections]
        H1[org_acme_corp]
        H2[org_demo]
    end
    
    A --> B
    B --> B1 & B2 & B3 & B4 & B5
    B1 & B2 & B3 & B4 --> C
    B5 --> D
    C --> E
    D --> F
    E & F --> G
    G --> G1 & G2
    C --> H
    H --> H1 & H2
    
    style A fill:#e1f5ff
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#f3e5f5
    style E fill:#e8f5e9
    style F fill:#e8f5e9
    style G fill:#fce4ec
    style H fill:#fce4ec
```
```

## Quick Template (Text-based for reference)

```
┌─────────────────────────────────────────┐
│          CLIENT APPLICATIONS            │
│      (Web, Mobile, External APIs)       │
└────────────────┬────────────────────────┘
                 │ HTTP/REST
                 │
┌────────────────▼────────────────────────┐
│         FASTAPI ROUTER LAYER            │
│  ┌────────────────────────────────┐     │
│  │ /org/create  /org/get          │     │
│  │ /org/update  /org/delete       │     │
│  │ /admin/login                   │     │
│  └────────────────────────────────┘     │
│              JWT Auth                   │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         SERVICE LAYER                   │
│  ┌──────────────┐  ┌──────────────┐    │
│  │Organization  │  │Auth Service  │    │
│  │Service       │  │              │    │
│  └──────────────┘  └──────────────┘    │
│    Business Logic & Validation          │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       REPOSITORY LAYER                  │
│  ┌──────────────┐  ┌──────────────┐    │
│  │Organization  │  │Admin         │    │
│  │Repository    │  │Repository    │    │
│  └──────────────┘  └──────────────┘    │
│       Data Access Abstraction           │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      MONGODB DATABASE LAYER             │
│  ┌─────────────────────────────────┐    │
│  │    MASTER DATABASE              │    │
│  │  • organizations (metadata)     │    │
│  │  • admin_users (credentials)    │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │  DYNAMIC COLLECTIONS            │    │
│  │  • org_acme_corp                │    │
│  │  • org_demo_company             │    │
│  │  • org_<organization_name>      │    │
│  └─────────────────────────────────┘    │
│     Multi-Tenant Data Isolation         │
└─────────────────────────────────────────┘
```

## After Creating

1. Save diagram as: `Croupier_Architecture_Diagram.png`
2. Place in root of repo
3. Update README.md to reference it:

```markdown
## Architecture

![Architecture Diagram](Croupier_Architecture_Diagram.png)

The system follows a layered architecture pattern with clear separation of concerns...
```

## Example Colors to Use

- **Client:** Light Blue (#e1f5ff)
- **API:** Light Orange (#fff3e0)
- **Service:** Light Purple (#f3e5f5)
- **Repository:** Light Green (#e8f5e9)
- **Database:** Light Pink (#fce4ec)

## Need More Detail?

For the assignment, include:
- ✅ Layer names
- ✅ Key components in each layer
- ✅ Flow arrows
- ✅ Multi-tenant structure
- ❌ Don't overcomplicate - keep it high-level!
