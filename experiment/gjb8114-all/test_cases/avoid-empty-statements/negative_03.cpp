int labeled_empty(bool flag) {
    int result = 0;
    if (flag) {
        goto done;
    }
    result = 1;
done: ; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-1]
    return result;
}
