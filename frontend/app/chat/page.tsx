'use client';

import * as React from 'react';
import { IconSend, IconRobot, IconUser, IconLoader } from '@tabler/icons-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { SidebarTrigger } from '@/components/ui/sidebar';
import { Separator } from '@/components/ui/separator';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from '@/components/ui/breadcrumb';
import { sendChatMessage } from '@/lib/api';
import type { ChatMessage, Product } from '@/lib/types';
import { ScrollArea } from '@/components/ui/scroll-area';

export default function ChatPage() {
  const [messages, setMessages] = React.useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI sales assistant. I can help you find the perfect parts for your customers. Try asking me about specific products, compatibility, or inventory.',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = React.useState('');
  const [isLoading, setIsLoading] = React.useState(false);
  const scrollRef = React.useRef<HTMLDivElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage(input, messages);
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response || response.message,
        products: response.products,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('[v0] Error sending message:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex h-screen flex-col">
      <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center gap-2 border-b bg-background px-4">
        <SidebarTrigger className="-ml-1" />
        <Separator orientation="vertical" className="mr-2 h-4" />
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbPage>Chat Assistant</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <div className="flex flex-1 flex-col overflow-hidden">
        <ScrollArea className="flex-1 p-6" ref={scrollRef}>
          <div className="mx-auto max-w-3xl space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    <IconRobot className="h-4 w-4" />
                  </div>
                )}
                <div className={`flex flex-col gap-2 ${message.role === 'user' ? 'items-end' : 'items-start'}`}>
                  <Card className={message.role === 'user' ? 'bg-primary text-primary-foreground' : ''}>
                    <CardContent className="p-4">
                      <p className="text-sm">{message.content}</p>
                    </CardContent>
                  </Card>
                  {message.products && message.products.length > 0 && (
                    <div className="flex flex-col gap-2">
                      {message.products.map((product: Product, pIndex: number) => (
                        <Card key={pIndex} className="max-w-md">
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2">
                                  <Badge variant="outline" className="text-xs">
                                    {product.sku}
                                  </Badge>
                                  {product.in_stock && (
                                    <Badge variant="default" className="text-xs">
                                      In Stock
                                    </Badge>
                                  )}
                                </div>
                                <h4 className="mt-2 font-medium">{product.product_name}</h4>
                                <p className="mt-1 text-sm text-muted-foreground">
                                  {product.brand} • {product.category}
                                </p>
                                <div className="mt-2 flex items-center gap-2">
                                  <span className="text-lg font-bold">
                                    ${product.sale_price.toFixed(2)}
                                  </span>
                                  {product.discount_percent && product.discount_percent > 0 && (
                                    <Badge variant="secondary" className="text-xs">
                                      {product.discount_percent}% off
                                    </Badge>
                                  )}
                                </div>
                              </div>
                              <Button size="sm" variant="outline">
                                View
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </div>
                {message.role === 'user' && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary text-secondary-foreground">
                    <IconUser className="h-4 w-4" />
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="flex gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                  <IconRobot className="h-4 w-4" />
                </div>
                <Card>
                  <CardContent className="p-4">
                    <IconLoader className="h-4 w-4 animate-spin" />
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </ScrollArea>

        <div className="border-t bg-background p-4">
          <form onSubmit={handleSubmit} className="mx-auto flex max-w-3xl gap-2">
            <Textarea
              placeholder="Ask about products, compatibility, or inventory..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              className="min-h-[60px] flex-1 resize-none"
            />
            <Button type="submit" size="icon" disabled={isLoading || !input.trim()}>
              <IconSend className="h-4 w-4" />
              <span className="sr-only">Send message</span>
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
