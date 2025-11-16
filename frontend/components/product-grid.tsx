'use client';

import * as React from 'react';
import { IconSearch } from '@tabler/icons-react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { Product } from '@/lib/types';

interface ProductGridProps {
  products: Product[];
}

export function ProductGrid({ products }: ProductGridProps) {
  const [searchQuery, setSearchQuery] = React.useState('');

  const filteredProducts = products.filter((product) =>
    product.product_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    product.sku.toLowerCase().includes(searchQuery.toLowerCase()) ||
    product.brand.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="relative">
        <IconSearch className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search products by name, SKU, or brand..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {filteredProducts.map((product) => (
          <Card key={product.sku} className="overflow-hidden transition-all hover:shadow-lg">
            <div className="aspect-square bg-gradient-to-br from-muted/50 to-muted flex items-center justify-center">
              <IconSearch className="h-12 w-12 text-muted-foreground" />
            </div>
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-2">
                <Badge variant="outline" className="text-xs">
                  {product.sku}
                </Badge>
                <Badge variant={product.in_stock ? 'default' : 'secondary'} className="text-xs">
                  {product.stock_status}
                </Badge>
              </div>
              <h3 className="mt-2 line-clamp-2 font-semibold leading-tight">
                {product.product_name}
              </h3>
              <p className="mt-1 text-sm text-muted-foreground">
                {product.brand}
              </p>
              <div className="mt-3 flex items-center justify-between">
                <div>
                  <span className="text-lg font-bold">
                    ${product.sale_price.toFixed(2)}
                  </span>
                  {product.discount_percent && product.discount_percent > 0 && (
                    <Badge variant="secondary" className="ml-2 text-xs">
                      {product.discount_percent}% off
                    </Badge>
                  )}
                </div>
              </div>
              <Button className="mt-4 w-full" size="sm">
                View Details
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredProducts.length === 0 && (
        <div className="flex flex-col items-center justify-center py-12">
          <p className="text-muted-foreground">No products found matching your search.</p>
        </div>
      )}
    </div>
  );
}
