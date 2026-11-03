// negative_08.cpp
thread_local int tls_requests; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-2]

int main()
{
    tls_requests += 1;
    return tls_requests;
}
