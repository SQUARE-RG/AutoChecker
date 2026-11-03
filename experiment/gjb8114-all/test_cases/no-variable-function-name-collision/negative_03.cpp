void process() {}

int main()
{
    for (int process = 0; process < 1; ++process) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-3]
        return process;
    }
    return 0;
}
