import React from 'react';
import { cn } from '../utils/helpers';

const Input = React.forwardRef(
  ({ error, label, helperText, container = 'mb-4', ...props }, ref) => {
    return (
      <div className={container}>
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}
        <input
          ref={ref}
          className={cn(
            'input-field',
            error && 'border-red-500 focus:ring-red-500'
          )}
          {...props}
        />
        {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
        {helperText && <p className="text-gray-500 text-sm mt-1">{helperText}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
