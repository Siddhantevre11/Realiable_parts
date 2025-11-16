'use client';

import * as React from 'react';
import { IconSearch, IconFilter } from '@tabler/icons-react';
import { SidebarTrigger } from '@/components/ui/sidebar';
import { Separator } from '@/components/ui/separator';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from '@/components/ui/breadcrumb';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { searchProducts } from '@/lib/api';
import type { Product } from '@/lib/types';

export default function SearchPage() {
  const [query, setQuery] = React.useState('');
  const [results, setResults] = React.useState<Product[]>([]);
  const [isSearching, setIsSearching] = React.useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    try {
      const data = await searchProducts(query);
      setResults(data.products || []);
    } catch (error) {
      console.error('[v0] Search error:', error);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="flex flex-col">
      <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center gap-2 border-b bg-background px-4">
        <SidebarTrigger className="-ml-1" />
        <Separator orientation="vertical" className="mr-2 h-4" />
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbPage>Search</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>
      
      <div className="flex-1 space-y-6 p-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Search Products</h1>
          <p className="text-muted-foreground">
            Find products using natural language or specific criteria
          </p>
        </div>

        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative flex-1">
            <IconSearch className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search for water filters, dishwasher parts, or describe what you need..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button type="submit" disabled={isSearching}>
            {isSearching ? 'Searching...' : 'Search'}
          </Button>
          <Button variant="outline" size="icon">
            <IconFilter className="h-4 w-4" />
          </Button>
        </form>

        {results.length > 0 && (
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Found {results.length} results
            </p>
            <div className="grid gap-4">
              {results.map((product) => (
                <Card key={product.sku}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{product.sku}</Badge>
                          <Badge variant={product.in_stock ? 'default' : 'secondary'}>
                            {product.stock_status}
                          </Badge>
                          {product.similarity && (
                            <Badge variant="secondary">
                              {Math.round(product.similarity * 100)}% match
                            </Badge>
                          )}
                        </div>
                        <h3 className="mt-2 text-lg font-semibold">
                          {product.product_name}
                        </h3>
                        <p className="mt-1 text-sm text-muted-foreground">
                          {product.brand} • {product.category}
                        </p>
                        {product.description && (
                          <p className="mt-2 text-sm">{product.description}</p>
                        )}
                        <div className="mt-3 flex items-center gap-4">
                          <span className="text-xl font-bold">
                            ${product.sale_price.toFixed(2)}
                          </span>
                          {product.discount_percent && product.discount_percent > 0 && (
                            <Badge variant="secondary">
                              {product.discount_percent}% off
                            </Badge>
                          )}
                        </div>
                      </div>
                      <Button>View Details</Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {!results.length && query && !isSearching && (
          <div className="flex flex-col items-center justify-center py-12">
            <p className="text-muted-foreground">No results found. Try a different search term.</p>
          </div>
        )}
      </div>
    </div>
  );
}
