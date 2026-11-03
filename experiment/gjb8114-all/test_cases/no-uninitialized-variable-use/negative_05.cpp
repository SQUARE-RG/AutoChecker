int main()
{
    double threshold;
    int status = 0;
    if (threshold > 0.0) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-1]
        status = 1;
    }
    return status;
}
