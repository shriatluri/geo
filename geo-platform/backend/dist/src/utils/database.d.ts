import { PrismaClient } from '@prisma/client';
declare global {
    var __prisma: PrismaClient | undefined;
}
export declare const prisma: PrismaClient<import(".prisma/client").Prisma.PrismaClientOptions, never, import("@prisma/client/runtime/library").DefaultArgs>;
export declare function checkDatabaseConnection(): Promise<boolean>;
export declare function disconnectDatabase(): Promise<void>;
export declare function getDatabaseMetrics(): Promise<{
    users: number;
    sites: number;
    analyses: number;
    timestamp: string;
    error?: never;
} | {
    users: number;
    sites: number;
    analyses: number;
    timestamp: string;
    error: string;
}>;
export default prisma;
//# sourceMappingURL=database.d.ts.map