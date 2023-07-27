// src/components/ProgressBar.js
import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faLeaf } from "@fortawesome/free-solid-svg-icons";

const ProgressBar = ({ percentage, totalLeaves }) => {
  const greenLeaves = Math.round((percentage * totalLeaves) / 100);
  const grayLeaves = totalLeaves - greenLeaves;

  return (
    <div className="flex items-center">
      {[...Array(greenLeaves)].map((_, index) => (
        <FontAwesomeIcon key={index} icon={faLeaf} className="text-2xl text-green-500" />
      ))}
      {[...Array(grayLeaves)].map((_, index) => (
        <FontAwesomeIcon key={index + greenLeaves} icon={faLeaf} className="text-2xl text-gray-400" />
      ))}
      <div className="ml-4 text-xl">{`${percentage}%`}</div>
    </div>
  );
};

export default ProgressBar;