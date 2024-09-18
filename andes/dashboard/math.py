import gascompressibility as gc

class Math():
    """
    This class let you get the current cuantity of matter in the bowl
    """
    def __init__(self, temperture, pressure):
        self.temperture = temperture,
        self.pressure = pressure,
        self.z = 0,
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
        self.z = gc.calc_z(Pr=P_r, Tr=T_r)
        return self.z        

    def molarVolume(self) ->float:
        """ 🟢
        When there's no extrem conditions: use the Z factor and change the ideal gasses P*Vmol = Z*R*T. After, clear Vmol:
        Vmol = (Z*R*T)/P, its magnitude is L/mol
        """
        Z = self.getZ()
        self.Vmol = (Z*0.082*self.temperture)/self.pressure
        return self.Vmol
    
    def gasQuantity(self) ->float:
        """ 🟢🟢
        1. Rho (ρ) is the density of the GLP = molar mass/molar volume. (g/L)
        2 Vmol means the specific volume.
        3. moles_quantity (n) =  define the cuantity of moles of glp gas. n= ρ*Vmol 
        4. available mass (m) = quantity
        """
        if self.Vmol >=1:
            density = (49.01)/self.Vmol
            moles_quantity = density*self.Vmol
            available_mass = moles_quantity*49.01
            return available_mass
        else:
            return 0