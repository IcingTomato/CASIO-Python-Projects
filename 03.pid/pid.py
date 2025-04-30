# PID Controller Implementation - MicroPython Version
import random

# Try to import hardware module for alternative random source
try:
    import machine
    has_machine = True
except ImportError:
    has_machine = False

class PID_Controller:
    def __init__(self, kp, ki, kd, target, output_min, output_max, integral_min, integral_max):
        # Control parameters
        self.kp = kp              # Proportional coefficient
        self.ki = ki              # Integral coefficient
        self.kd = kd              # Derivative coefficient
        
        self.target = target      # Target value
        
        self.error_sum = 0.0      # Error accumulation (for integral term)
        self.last_error = 0.0     # Previous error (for derivative term)
        
        self.output_max = output_max    # Output upper limit
        self.output_min = output_min    # Output lower limit
        self.integral_max = integral_max  # Integral term upper limit
        self.integral_min = integral_min  # Integral term lower limit
        
        self.initialized = False  # Whether initialized

    def reset(self):
        """Reset PID controller"""
        self.error_sum = 0.0
        self.last_error = 0.0
        self.initialized = False
    
    def calculate(self, current_value, dt):
        """Calculate PID output value"""
        # Calculate error
        error = self.target - current_value
        
        # Proportional term
        p_term = self.kp * error
        
        # Integral term
        self.error_sum += error * dt
        
        # Integral limiting
        if self.error_sum > self.integral_max:
            self.error_sum = self.integral_max
        elif self.error_sum < self.integral_min:
            self.error_sum = self.integral_min
        
        i_term = self.ki * self.error_sum
        
        # Derivative term
        d_term = 0.0
        if self.initialized:
            d_term = self.kd * ((error - self.last_error) / dt)
        
        # Update last_error and initialized
        self.last_error = error
        self.initialized = True
        
        # Calculate total output
        output = p_term + i_term + d_term
        
        # Output limiting
        if output > self.output_max:
            output = self.output_max
        elif output < self.output_min:
            output = self.output_min
        
        return output, p_term, i_term, d_term
    
    def set_target(self, new_target):
        """Set new target value"""
        self.target = new_target

# Alternative random seed generation function
def get_alternative_seed():
    seed = 0
    
    # Try to get randomness from multiple sources
    if has_machine:
        try:
            # Try to read noise from ADC
            adc = machine.ADC(0)  # Use ADC0 pin
            for i in range(5):
                seed = (seed * 37 + adc.read()) & 0xFFFFFFFF
        except:
            pass
            
        try:
            # Try to use counter
            seed = (seed * 17 + machine.unique_id()[0]) & 0xFFFFFFFF
        except:
            pass
    
    # Use a simple incrementing counter as part of the seed
    global counter
    counter = (counter * 7 + 13) & 0xFFFFFFFF
    seed = (seed * 11 + counter) & 0xFFFFFFFF
    
    return seed

# Global counter, used as a simple seed source
counter = 1234

def main():
    # Initialize random number generator
    seed = get_alternative_seed()
    random.seed(seed)
    print("Using random seed: {}".format(seed))
    
    # Create and initialize PID controller
    pid = PID_Controller(
        kp=2.0, ki=0.5, kd=0.25,           # PID parameters
        target=100.0,                       # Target value
        output_min=-1000.0, output_max=1000.0,  # Output limits
        integral_min=-100.0, integral_max=100.0  # Integral limits
    )
    
    # Simulated system variables
    current_value = 0.0
    control_output = 0.0
    dt = 0.1  # Time step 100ms
    iteration = 0
    
    # Simple simulation - infinite loop
    print("Time\tTarget\tCurrent\tOutput\tP-Term\tI-Term\tD-Term")
    
    while True:  # Infinite loop
        # Calculate control amount
        control_output, p_term, i_term, d_term = pid.calculate(current_value, dt)
        
        # Simulate system response (simplified model)
        current_value += control_output * 0.01
        
        # Output current state - using .format() instead of f-string
        print("{:.1f}\t{:.1f}\t{:.1f}\t{:.1f}\t{:.1f}\t{:.1f}\t{:.1f}".format(
            iteration * dt, pid.target, current_value, control_output, p_term, i_term, d_term))
        
        # Change target value every 50 iterations, using new random seed
        if iteration % 50 == 0 and iteration > 0:
            seed = get_alternative_seed()
            random.seed(seed)
            new_target = float(random.randint(0, 199))  # Random target value in range 0-199
            pid.set_target(new_target)
            print("--- Seed: {}, Target changed to {:.1f} ---".format(seed, new_target))
        
        iteration += 1
        
        # Add delay - using simple delay function
        for _ in range(1000000):  # Simple delay loop
            pass

if __name__ == "__main__":
    main()