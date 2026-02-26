import React from 'react';
import { getAvatarColor, getInitials } from '../utils/helpers';

const Avatar = ({
  name = 'User',
  image = null,
  size = 'md',
  index = 0,
  className = '',
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
    xl: 'w-16 h-16 text-lg',
  };

  if (image) {
    return (
      <img
        src={image}
        alt={name}
        className={`${sizeClasses[size]} rounded-full object-cover ${className}`}
      />
    );
  }

  return (
    <div
      className={`${sizeClasses[size]} ${getAvatarColor(index)} rounded-full flex items-center justify-center text-white font-bold ${className}`}
    >
      {getInitials(name.split(' ')[0], name.split(' ')[1])}
    </div>
  );
};

export default Avatar;
