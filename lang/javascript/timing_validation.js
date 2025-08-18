const validate_timing_validation = () => {
    const start = Date.now();
    for (let i = 0; i < 1000; i++) {}
    return Date.now() - start < 10;
};

console.assert(validate_timing_validation());
