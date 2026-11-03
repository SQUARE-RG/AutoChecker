namespace cfg {
extern int limit = 10; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-19]
}

int main()
{
    cfg::limit = 20;
    return cfg::limit;
}
