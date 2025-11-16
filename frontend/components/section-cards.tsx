import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { IconTrendingUp, IconPackage, IconShoppingCart, IconCurrencyDollar } from '@tabler/icons-react';
import type { Analytics } from '@/lib/types';

interface SectionCardsProps {
  analytics: Analytics;
}

export function SectionCards({ analytics }: SectionCardsProps) {
  const cards = [
    {
      title: 'Total Products',
      value: analytics.total_products.toString(),
      description: 'Total Products',
      badge: '+12.5%',
      footer: 'Trending up this month',
      icon: IconPackage,
      gradient: 'from-primary/10 to-card'
    },
    {
      title: 'In Stock',
      value: `${analytics.in_stock_count} (${analytics.in_stock_percentage.toFixed(1)}%)`,
      description: 'Available Now',
      badge: '+5%',
      footer: 'Strong inventory levels',
      icon: IconShoppingCart,
      gradient: 'from-chart-2/10 to-card'
    },
    {
      title: 'Average Price',
      value: `$${analytics.avg_price.toFixed(2)}`,
      description: 'Average Price',
      badge: '+2.3%',
      footer: 'Price optimization working',
      icon: IconCurrencyDollar,
      gradient: 'from-chart-3/10 to-card'
    },
    {
      title: 'Top Category',
      value: analytics.category_distribution[0]?.category.replace(' Parts', '') || 'N/A',
      description: `${analytics.category_distribution[0]?.count || 0} products`,
      badge: 'Top Seller',
      footer: 'Most popular category',
      icon: IconTrendingUp,
      gradient: 'from-chart-4/10 to-card'
    }
  ];

  return (
    <div className="grid grid-cols-1 gap-4 @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
      {cards.map((card, index) => (
        <Card
          key={index}
          className={`bg-gradient-to-t ${card.gradient} shadow-sm @container/card`}
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {card.description}
            </CardTitle>
            <card.icon className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold @[250px]/card:text-3xl">
              {card.value}
            </div>
            <div className="mt-2 flex items-center gap-2">
              <Badge variant="secondary" className="text-xs">
                <IconTrendingUp className="mr-1 size-3" />
                {card.badge}
              </Badge>
            </div>
            <p className="mt-2 text-xs text-muted-foreground">{card.footer}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
