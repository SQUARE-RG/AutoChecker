int main()
{
    int state = 2;
    switch (state) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-5]
        default:
            if (state != 0) {
                state = 0;
            }
    }
    return state;
}
