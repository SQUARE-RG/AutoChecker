int call_variadic(int (*cb)(int, ...), int arg) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-15]
    return cb(arg);
}

int main()
{
    return 0;
}
