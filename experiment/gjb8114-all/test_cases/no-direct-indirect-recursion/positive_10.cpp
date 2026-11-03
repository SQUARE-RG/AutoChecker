#include <cstdbool>

int calibrate(int raw);

class Sensor {
public:
    int read(int raw) {
        return calibrate(raw);
    }
};

int calibrate(int raw) {
    return raw * 2;
}

int main() {
    Sensor s;
    return s.read(3) - 6;
}
