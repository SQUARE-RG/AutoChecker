int switch_empty(int value) {
    int result = 0;
    switch (value) {
    case 0:
        ; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-1]
        break;
    default:
        result = 1;
        break;
    }
    return result;
}
