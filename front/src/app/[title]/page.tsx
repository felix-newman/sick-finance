import { Button } from "@/components/ui/button";
import { Article, getGeneratedArticleByTitle } from "@/lib/api/articleGateway";
import Link from "next/link";
import Image from 'next/image'

export default async function Home({ params }: { params: { title: string } }) {
    
    const article = await getGeneratedArticleByTitle(params.title);
    
    return (
        <div>
            <div className="container mx-auto p-4">
                <div className="max-w-[50%] mx-auto">
                    <h1>{article.title}</h1>
                    <p>{article.lead}</p>
                    <Image
                    width={350}
                    height={350}
                    src={`data:image/jpeg;base64,${article.image_data}`} 
                    alt={article.title} 
                    className="my-4" />
                    {/* <div>{article}</div> */}
                    <ul>
                        {article.mentioned_stocks?.map(stock => (
                          <li key={stock}>{stock}</li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    )
}