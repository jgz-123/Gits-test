#include <fstream>
#include <iostream>
#include <string>

int main() {
    const char* paths[] = {"workspace/runtime.txt", "workspace/data/labels.txt"};
    for (const auto* path : paths) {
        std::ifstream file(path);
        std::string line;
        if (!std::getline(file, line)) {
            std::cerr << "Missing delivery file: " << path << "\n";
            return 1;
        }
        std::cout << path << ": " << line << "\n";
    }
    std::cout << "Delivery smoke test passed (no model inference).\n";
}
