import gascompressibility as gc

class Math():
    """
    This class let you get the current cuantity of matter in the bowl
    """
    def __init__(self, temperture, pressure):
        self.temperture = temperture
        self.pressure = pressure
        self.z = 0
        self.Vmol = 0
    
    def getZ(self) -> float:
        """
        constants:
        The critical pressure is calculated as (65% * propane critical pressure) + (35% * butane critical pressure).
        The critical temperature is calculated as (65% * propane critical temp) + (35% * butane critical temp).
        """
        Pc = 40.24 # atm
        Tc = 389.18 # °K
        # It's necessary to get the compression factor
        P_r = self.pressure/Pc
        T_r = self.temperture/Tc
        # get the compression factor, Z
        try:
            self.z = gc.calc_z(Pr=P_r, Tr=T_r)
        except Exception as e:
            raise e
        return self.z        
    
    def gasQuantity(self, total_volume) ->float:
        """ 🟢🟢
        1. if the pressure increases, the quantity of moles too because is the output pressure.
        2. Use PV = znRT and clear n to get the quantity of gas.
        3. n = P*V / zRT
        """
        if self.pressure > 0:
            self.z = self.getZ()
            n=(self.pressure*total_volume)/(self.z*0.082*self.temperture)
            return n
        else:
            return 0
        
    def avogadro_law(self, total_volume, total_mol, current_mol):
        """
        This function let us find the current volume of gas
        V1/n1 = V2/n2
        V1 and n1 is the initial moment and V2 and n2 is the current volume
        """
        current_volume = (total_volume*current_mol)/total_mol
        return current_volume
        
    def maxGasQuantity(self, masa) -> float:
        """
        Just excecute to set the max capacity
        """
        max_gas = self.molarVolume()
        
        n = masa/49.01
        max_gas_cuantity = n*max_gas
        return max_gas_cuantity