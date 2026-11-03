struct {
    signed long int low : 4;
    unsigned long int high : 4;
} data;

int main() {
    data.low = 1;
    data.high = 1;
    return 0;
}
