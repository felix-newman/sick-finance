import { Button } from "@/components/ui/button";
import { Article } from "@/lib/api/articleGateway";
import Link from "next/link";
import Image from 'next/image'

export default async function Home({ params }: { params: { title: string } }) {
    const article: Article = {
        id: "1",
        title: "Hello World",
        lead: "This is a dummy article",
        imgUrl: "/exmaple.png",
        stocks: ["AAPL", "GOOGL", "AMZN"],
        sourceUrl: "https://google.com", // added missing comma
        text: "This is a dummy article"
    }
    return (
        <div>
            <div className="container mx-auto p-4">
                <div className="max-w-[50%] mx-auto">
                    <h1>{article.title}</h1>
                    <p>{article.lead}</p>
                    <Image 
                    width={350}
                    height={350}
                    src={article.imgUrl!} 
                    alt={article.title} 
                    className="my-4" />
                    <div>{article.text}</div>
                    <ul>
                        {article.stocks.map(stock => (
                          <li key={stock}>{stock}</li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    )
}