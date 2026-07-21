import React, { useState, useEffect } from "react";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";


dayjs.extend(relativeTime);
dayjs.extend(utc);


// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */

  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [now, setNow] = useState(dayjs());
  const [likes, setLikes] = useState("");
  const [created, setCreated] = useState("");
  const [showUrl, setShowUrl] = useState("");

  useEffect(() => {
    const timer = setInterval(() => {
      setNow(dayjs());
    }, 60000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          setLikes(data.likes);
          setCreated(data.created)
          setShowUrl(data.postShowUrl);
        }
      })
      .catch((error) => console.log(error));
    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);
  
  function handleClick(){
    setLikes((prevLikes) => ({
    ...prevLikes,
    numLikes: prevLikes.lognameLikesThis
      ? prevLikes.numLikes - 1
      : prevLikes.numLikes + 1,
    lognameLikesThis: !prevLikes.lognameLikesThis,
  }));
  }

  // Render post image and post owner
  return (
    <div className="post">
      <img src={imgUrl} alt="post_image"/>
      <p>{owner}</p>
      <a href={showUrl} data-testid="post-time-ago">
        {dayjs.utc(created).fromNow()}
      </a>
      <button data-testid="like-unlike-button" onClick = {handleClick}>
      {likes.lognameLikesThis ? "Unlike" : "Like"}
      </button>
      <p>{likes.numLikes} {likes.numLikes == 1 ? "like" : "likes"} </p>
    </div>
  );
}
