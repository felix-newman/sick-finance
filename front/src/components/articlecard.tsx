import { cn } from "@/lib/utils";
import Link from "next/link";
import { JSX } from "react";
import { Button } from "./ui/button";
import { Article, GeneratedArticle } from "@/lib/api/articleGateway";
import Image from 'next/image'
import { Badge } from "./ui/badge";

interface ArticleCardProps {
    title: string;
    description: string;
    imageData: string;
    stocks: string[];
    onClick: () => void;
}

export default function ArticleCard({ title, description, imageData, stocks, onClick }: ArticleCardProps) {
    return (
        <div 
            className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden cursor-pointer hover:shadow-md transition-shadow"
            onClick={onClick}
        >
            {imageData && (
                <div className="w-full h-48 relative">
                    <img 
                        src={`data:image/jpeg;base64,${imageData}`}
                        alt={title}
                        className="w-full h-full object-cover"
                    />
                </div>
            )}
            <div className="p-4">
                <h2 className="text-xl font-semibold mb-2">
                    {title}
                </h2>
                <p className="text-gray-600 mb-3">
                    {description}
                </p>
                <div className="flex flex-wrap gap-1">
                    {stocks.map((stock, index) => (
                        <Badge key={index}>
                            {stock}
                        </Badge>
                    ))}
                </div>
            </div>
        </div>
    );
}
