#define NET_TIMEOUT 30

int legacy_timeout(void)
{
    return NET_TIMEOUT;
}

#define NET_TIMEOUT \
    60 // CHECK-MESSAGES: :[[@LINE-1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-5]

int main(void)
{
    return legacy_timeout() + NET_TIMEOUT;
}
