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
                    <div className="">
                        <img
                            width={200}
                            height={200}
                            src={`data:image/jpeg;base64,${article.image_data}`}
                            alt={article.title}
                            className="my-4 mx-auto" />
                    </div>

                    <h1 className="text-4xl font-bold">{article.title}</h1>


                    <blockquote className="my-4 ml-[0.075em] border-l-3 border-gray-300 pl-4 text-gray-700">{article.lead}</blockquote>


                    <p className="text-gray-800 leading-snug">{article.content}</p>

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