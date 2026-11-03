void clear_buffer(int* data) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-5]
{
    for (int i = 0; i < 8; ++i) {
        data[i] = 0;
    }
}

int main()
{
    int buffer[8] = {};
    clear_buffer(buffer);
    return 0;
}
