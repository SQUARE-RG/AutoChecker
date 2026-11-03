struct Packet
{
    unsigned char header;
    struct Payload final { unsigned char code; unsigned char len; } payload;
};

int main()
{
    Packet packet;
    packet.header = 2;
    packet.payload.code = 3;
    packet.payload.len = 4;
    return 0;
}
