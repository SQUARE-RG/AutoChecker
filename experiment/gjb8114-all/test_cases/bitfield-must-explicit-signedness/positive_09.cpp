struct Data {
    signed short int low : 3;
    unsigned short int high : 3;
};

int main() {
    Data data{};
    data.low = 1;
    data.high = 1;
    return 0;
}
