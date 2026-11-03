void compute() {}

int main()
{
    if (int compute = 0; compute == 0) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-3]
        return compute;
    }
    return 0;
}
