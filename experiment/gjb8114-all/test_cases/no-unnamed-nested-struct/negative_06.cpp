struct Packet
{
    unsigned char header;
    struct Payload final { unsigned char code; unsigned char len; };  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-9]
};

int main()
{
    Packet packet;
    packet.header = 2;
    return 0;
}
