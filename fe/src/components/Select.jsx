import React from 'react';
import { cn } from '../utils/helpers';

const Select = React.forwardRef(
  ({ error, label, options = [], helperText, container = 'mb-4', ...props }, ref) => {
    return (
      <div className={container}>
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}
        <select
          ref={ref}
          className={cn(
            'input-field',
            error && 'border-red-500 focus:ring-red-500'
          )}
          {...props}
        >
          <option value="">Select an option</option>
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
          {/* Render any children passed (allows JSX <option> elements) */}
          {props.children}
        </select>
        {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
        {helperText && <p className="text-gray-500 text-sm mt-1">{helperText}</p>}
      </div>
    );
  }
);

Select.displayName = 'Select';

export default Select;
