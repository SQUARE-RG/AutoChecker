void increment(int (*values)[4]) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-1]
{
    for (int i = 0; i < 4; ++i) {
        (*values)[i] += 1;
    }
}

int main() {
    int data[4] = {0, 1, 2, 3};
    increment(&data);
    return 0;
}
