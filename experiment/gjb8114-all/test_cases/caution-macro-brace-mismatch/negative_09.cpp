#define OPEN_NS(ns) namespace ns { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-2]

OPEN_NS(test_ns)
int value = 1;
}

int main()
{
    return 0;
}
