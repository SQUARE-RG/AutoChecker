// positive_08.cpp
thread_local int tls_requests = 0;

int main()
{
    tls_requests += 1;
    return tls_requests;
}
