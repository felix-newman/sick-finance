import { Button } from "@/components/ui/button";
import { Article, getGeneratedArticleByTitle } from "@/lib/api/articleGateway";
import Link from "next/link";
import Image from 'next/image'
import { Badge } from "@/components/ui/badge";

export default async function Home({ params }: { params: { title: string } }) {

    const article = await getGeneratedArticleByTitle(params.title);

    return (
        <div>
            <div className="container mx-auto p-4">
                <div className="max-w-[50%] mx-auto">
                    <div className="mb-6">
                        <h1 className="text-4xl font-bold mb-4">{article.title}</h1>
                        <div className="relative w-full h-[200px] overflow-hidden">
                            <img
                                className="w-full absolute top-0 left-0 object-cover"
                                style={{ height: '400px', marginTop: '0' }}
                                src={`data:image/jpeg;base64,${article.image_data}`}
                                alt={article.title} />
                        </div>
                        
                        <p className="text-xl text-gray-600 font-medium mb-6">{article.lead}</p>
                    </div>

                    <p className="text-gray-800 leading-snug">{article.content}</p>
                    <div className="flex flex-wrap gap-1">
                        {article.mentioned_stocks?.map(stock => (
                            <Badge key={stock}>
                                {stock}
                            </Badge>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}