int g_numerator = 20;
int g_denominator = 6;
int g_result = 0;

void compute_average() {
    g_result = g_numerator / g_denominator; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-2]
}

int main() {
    compute_average();
    return 0;
}
