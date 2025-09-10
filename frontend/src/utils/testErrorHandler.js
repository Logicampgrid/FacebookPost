// Test file to verify error handling works correctly
import { formatErrorMessage, handleAxiosError, safeErrorDisplay } from './errorHandler';

// Test the error handler with various types of error objects
export const testErrorHandling = () => {
  console.log('=== Testing Error Handler ===\n');

  // Test 1: FastAPI validation error object
  const validationError = {
    type: 'value_error',
    loc: ['body', 'email'],
    msg: 'field required',
    input: { name: 'test' },
    url: 'https://pydantic-docs.helpmanual.io/usage/validators/'
  };
  
  console.log('Test 1 - FastAPI validation error:');
  console.log('Input:', validationError);
  console.log('Output:', formatErrorMessage(validationError));
  console.log('Safe display:', safeErrorDisplay(validationError));
  console.log('\n');

  // Test 2: Array of validation errors
  const validationErrors = [
    {
      type: 'value_error',
      loc: ['body', 'email'],
      msg: 'field required'
    },
    {
      type: 'value_error', 
      loc: ['body', 'password'],
      msg: 'ensure this value has at least 8 characters'
    }
  ];

  console.log('Test 2 - Array of validation errors:');
  console.log('Input:', validationErrors);
  console.log('Output:', formatErrorMessage(validationErrors));
  console.log('\n');

  // Test 3: Axios error simulation
  const axiosError = {
    isAxiosError: true,
    response: {
      status: 422,
      data: {
        detail: validationError
      }
    }
  };

  console.log('Test 3 - Axios error with validation:');
  console.log('Input:', axiosError);
  console.log('Output:', handleAxiosError(axiosError));
  console.log('\n');

  // Test 4: Network error
  const networkError = {
    code: 'NETWORK_ERROR',
    message: 'Network Error'
  };

  console.log('Test 4 - Network error:');
  console.log('Input:', networkError);
  console.log('Output:', handleAxiosError(networkError));
  console.log('\n');

  // Test 5: String error
  const stringError = 'Simple error message';
  console.log('Test 5 - String error:');
  console.log('Input:', stringError);
  console.log('Output:', formatErrorMessage(stringError));
  console.log('\n');

  // Test 6: Null/undefined
  console.log('Test 6 - Null/undefined:');
  console.log('null:', formatErrorMessage(null));
  console.log('undefined:', formatErrorMessage(undefined));
  console.log('\n');

  console.log('=== Error Handler Tests Complete ===');
};

// Run tests if this file is imported in development
if (process.env.NODE_ENV === 'development') {
  // Uncomment to run tests automatically
  // testErrorHandling();
}