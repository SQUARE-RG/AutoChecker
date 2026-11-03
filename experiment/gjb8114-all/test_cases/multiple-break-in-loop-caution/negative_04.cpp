int bounded_scan(int target, int maxSteps) {
    int step = 0;
    int result = -1;
    do {
        if (step == target) {
            result = step;
            break;
        }
        if (step >= maxSteps) {
            result = maxSteps;
            break; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-2]
        }
        ++step;
    } while (step < maxSteps);
    return result;
}
