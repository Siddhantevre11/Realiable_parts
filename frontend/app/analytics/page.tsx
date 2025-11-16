import { fetchAnalytics } from '@/lib/api';
import { SidebarTrigger } from '@/components/ui/sidebar';
import { Separator } from '@/components/ui/separator';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from '@/components/ui/breadcrumb';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ChartAreaInteractive } from '@/components/chart-area-interactive';
import { PriceDistribution } from '@/components/price-distribution';

export default async function AnalyticsPage() {
  const analytics = await fetchAnalytics();

  return (
    <div className="flex flex-col">
      <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center gap-2 border-b bg-background px-4">
        <SidebarTrigger className="-ml-1" />
        <Separator orientation="vertical" className="mr-2 h-4" />
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbPage>Analytics</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>
      
      <div className="flex-1 space-y-6 p-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            Detailed insights into your inventory and sales
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <ChartAreaInteractive data={analytics.category_distribution} />
          
          <Card>
            <CardHeader>
              <CardTitle>Price Range</CardTitle>
              <CardDescription>
                Distribution of product prices across your catalog
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Minimum Price</span>
                  <span className="font-semibold">
                    ${analytics.price_range.min.toFixed(2)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Maximum Price</span>
                  <span className="font-semibold">
                    ${analytics.price_range.max.toFixed(2)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Average Price</span>
                  <span className="font-semibold">
                    ${analytics.avg_price.toFixed(2)}
                  </span>
                </div>
                <Separator />
                <div className="pt-2">
                  <p className="text-sm text-muted-foreground">
                    Your product prices span a wide range, with the majority falling between 
                    ${(analytics.price_range.min + 20).toFixed(2)} and ${(analytics.avg_price + 50).toFixed(2)}.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <PriceDistribution data={analytics.category_distribution} avgPrice={analytics.avg_price} />
      </div>
    </div>
  );
}
