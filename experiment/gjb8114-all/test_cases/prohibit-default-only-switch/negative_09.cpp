int main()
{
    int mode = 1;
    switch (mode) default: mode = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-5]
    return mode;
}
