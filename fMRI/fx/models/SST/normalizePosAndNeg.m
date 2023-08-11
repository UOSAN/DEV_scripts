

function newArray = normalizePosAndNeg(inputArray)
    % Initialize the new array to the same values as the input array
    newArray = inputArray;

    % Get the sum of the positive values
    posSum = sum(inputArray(inputArray > 0));

    % Divide positive values by the sum of all the positives  
    newArray(inputArray > 0) = inputArray(inputArray > 0) / posSum; 

    % Get the sum of the negative values (it will be a negative number)
    negSum = sum(inputArray(inputArray < 0));

    % Divide negative values by the sum of all the negatives
    newArray(inputArray < 0) = inputArray(inputArray < 0) / abs(negSum); 

end