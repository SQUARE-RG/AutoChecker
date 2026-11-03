enum Packet
{
    Empty,
    Header = sizeof(int), // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-4]
    Payload,
    Trailer
};

int main()
{
    Packet p = Payload;
    return static_cast<int>(p);
}
