import Post from "./post";
import React, { useState, useEffect } from "react";

export default function Feed() {
    const [posts, setPosts] = useState(null);
    const [nextUrl, setNext] = useState("/api/v1/posts/");
    const [hasMore, setMore] = useState(true);

    useEffect(() => {
        // Declare a boolean flag that we can use to cancel the API request.
        let ignoreStaleRequest = false;

        if (!nextUrl) return () => {};
        // Call REST API to get the next 10 posts information
        fetch(nextUrl, { credentials: "same-origin" })
        .then((response) => {
            if (!response.ok) throw Error(response.statusText);
            return response.json();
        })
        .then((data) => {
            // If ignoreStaleRequest was set to true, we want to ignore the results of the
            // the request. Otherwise, update the state to trigger a new render.
            if (!ignoreStaleRequest) {
            setPosts((currPosts) => [...(currPosts || []), ...data.results]);
            setNext(data.next || null);
            setMore(Boolean(data.next));
            }
        })
        .catch((error) => console.log(error));
        

        return () => {
            // This is a cleanup function that runs whenever the Post component
            // unmounts or re-renders. If a Post is about to unmount or re-render, we
            // should avoid updating state.
            ignoreStaleRequest = true;
        };
    }, [nextUrl]);
    if (posts == null){
        return <div className="post">Loading...</div>;
    }

    return (
        <div className="feed">
            {posts.map((post) => (
                <Post key={post.postid} url={post.url}></Post>
            ))}
        </div>
    );
}