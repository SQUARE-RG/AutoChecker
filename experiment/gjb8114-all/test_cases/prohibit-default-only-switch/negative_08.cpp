int find(int value)
{
    switch (value) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-5]
        default:
            goto done;
    }
done:
    return value;
}
