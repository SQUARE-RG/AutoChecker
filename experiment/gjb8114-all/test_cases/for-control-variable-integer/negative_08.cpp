int main() {
    double result = 0.0;
    for (float value = 0.0f, step = 0.25f; value < 4.0f; value += step) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-2]
    {
        result += value;
    }
    return result > 0.0 ? 0 : 0;
}
