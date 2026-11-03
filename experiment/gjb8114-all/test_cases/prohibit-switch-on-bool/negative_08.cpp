int main()
{
    bool ready = true;
    int state = 0;
    switch (!ready) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-4]
        case true:
            state = 1;
            break;
        case false:
            state = 2;
            break;
    }
    return state;
}
