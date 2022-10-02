import * as React from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Divider from '@mui/material/Divider';
import Button from '@mui/material/Button';
import PropTypes from 'prop-types';
import { styled, Stack, Container, Slider, Typography, Tooltip, Menu, MenuItem, TextField } from '@mui/material';
import CreateIcon from '@mui/icons-material/Create';
import FileUploadIcon from '@mui/icons-material/FileUpload';
import TaskIcon from '@mui/icons-material/Task';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import { alignProperty } from '@mui/material/styles/cssUtils';


function ValueLabelComponent(props) {
    const { children, value } = props;
  
    return (
      <Tooltip enterTouchDelay={0} placement="top" title={value}>
        {children}
      </Tooltip>
    );
}
  
ValueLabelComponent.propTypes = {
    children: PropTypes.element.isRequired,
    value: PropTypes.number.isRequired,
};

const MenuButton = styled(Button)({
    //color:'black',
    textTransform:'none',
    fontSize:16,
});

const TXT = () => (
<Box>
<Box component="form" noValidate autoComplete="off">
    <TextField id="standard-basic" label="Text" variant="standard" />
</Box>
 <Box sx={{display:'flex', justifyContent:'center', marginTop:3}}>
    <CustomButton variant="contained" endIcon={<NavigateNextIcon />}>Next</CustomButton>
 </Box>
 </Box>
);

const CUST = () => (
    <Box sx={{display:'flex', justifyContent:'center'}}>
        <UpBtn/>
    </Box>
);

const UpBtn = () => (
    <CustomButton variant="contained" startIcon={<FileUploadIcon />} component="label">Tile image(s)
    <input hidden accept="image/*" multiple type="file" />
    </CustomButton>
);

const NxtBtn = () => (
    <CustomButton variant="contained" endIcon={<NavigateNextIcon />}>Next</CustomButton>
);


function CustomMenu(){
    const [txt, setTxt] = React.useState(true);
    const [cust, setCust] = React.useState(false);

    const [anchorEl, setAnchorEl] = React.useState(null);
    const open = Boolean(anchorEl);
    const handleClick = (event) => {
      setAnchorEl(event.currentTarget);
    };
    const handleClose = () =>{
        setAnchorEl(null);
    }
    const handleClose1 = () => {
      setAnchorEl(null);
      setTxt(true);
      setCust(false);
    };
    const handleClose2 = () => {
        setAnchorEl(null);
        setTxt(false);
        setCust(true);
    };

    return (
    <Stack direction="column" spacing={3} sx={{width:180}}>
    <Box sx={{display:'flex', justifyContent:'center'}}>
    <div>
        <MenuButton
          id="basic-button"
          aria-controls={open ? 'basic-menu' : undefined}
          aria-haspopup="true"
          aria-expanded={open ? 'true' : undefined}
          onClick={handleClick}
          variant="contained"
          disableElevation
          endIcon={<KeyboardArrowDownIcon />}
        >
          Mode
        </MenuButton>
        <Menu
          id="basic-menu"
          anchorEl={anchorEl}
          open={open}
          onClose={handleClose}
          MenuListProps={{
            'aria-labelledby': 'basic-button',
          }}
        >
          <MenuItem onClick={handleClose1}>Text</MenuItem>
          <MenuItem onClick={handleClose2}>Custom Images</MenuItem>
        </Menu>
      </div>
    </Box>
    {txt === true && <TXT/>}
    {cust === true && <CUST/>}
    </Stack>
    );
}


const AddTextField = () => (
    <Stack direction="column" spacing={3} sx={{width:180}}>
    <Box sx={{display:'flex', justifyContent:'center'}}>
    <BasicMenu/>
    </Box>
    {/* <Box component="form" noValidate autoComplete="off">
         <TextField id="standard-basic" label="Text" variant="standard" />
    </Box>
    <Box sx={{display:'flex', justifyContent:'center'}}>
    <CustomButton variant="contained" disabled endIcon={<NavigateNextIcon />}>Next</CustomButton>
    </Box> */}
    <TXT/>
    </Stack>
);

function BasicMenu() {
    const [anchorEl, setAnchorEl] = React.useState(null);
    const open = Boolean(anchorEl);
    const handleClick = (event) => {
      setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
      setAnchorEl(null);
    };
  
    return (
      <div>
        <MenuButton
          id="basic-button"
          aria-controls={open ? 'basic-menu' : undefined}
          aria-haspopup="true"
          aria-expanded={open ? 'true' : undefined}
          onClick={handleClick}
          variant="contained"
          disableElevation
          endIcon={<KeyboardArrowDownIcon />}
        >
          Mode
        </MenuButton>
        <Menu
          id="basic-menu"
          anchorEl={anchorEl}
          open={open}
          onClose={handleClose}
          MenuListProps={{
            'aria-labelledby': 'basic-button',
          }}
        >
          <MenuItem onClick={handleClose}>Text</MenuItem>
          <MenuItem onClick={handleClose}>Custom Images</MenuItem>
        </Menu>
      </div>
    );
  }

///const darkTheme = createTheme({ palette: { mode: 'dark' } });
const CustomButton = styled(Button)({
    textTransform:'none',
    fontSize:16,
    borderRadius:18,
});


const ChooseMode = (props) => (
    <Stack direction="row" spacing={2}  divider={<Divider orientation="vertical" flexItem />}>
        <CustomButton variant="contained" startIcon={<CreateIcon />} onClick={props.handler}>Random Mosaic</CustomButton>
        <CustomButton variant="contained" startIcon={<CreateIcon />}>Custom Mosaic</CustomButton>
    </Stack>
);

const UploadMode = () => (
    <CustomButton variant="contained" startIcon={<FileUploadIcon />} component="label">
        Upload Image
        <input hidden accept="image/*" multiple type="file" />
    </CustomButton>
);

const GenerateMode = () => (
<Stack direction="column" spacing={4} sx={{width:320}}>
<Stack direction="column" spacing={1}  divider={<Divider orientation="horizontal" flexItem />}>
    <Box>
      <Typography gutterBottom>Tile width</Typography>
      <Slider
        valueLabelDisplay="auto"
        components={{
          ValueLabel: ValueLabelComponent,
        }}
        aria-label="custom thumb label"
        defaultValue={20}
      />
    </Box>
    <Box>
      <Typography gutterBottom>Tile height</Typography>
      <Slider
        valueLabelDisplay="auto"
        components={{
          ValueLabel: ValueLabelComponent,
        }}
        aria-label="custom thumb label"
        defaultValue={20}
      />
    </Box>
</Stack>
<Box sx={{display:'flex',justifyContent:'center'}}>
<CustomButton variant="contained" startIcon={<TaskIcon />} sx={{width:240}}>Create Mosaic</CustomButton>
</Box>
</Stack>
);

function CustomGenerate(){
    const [one, setOne] = React.useState(true);
    const [two, setTwo] = React.useState(false);

    const handleClick = () => {
        setOne(false);
        setTwo(true);
    };

    return(
        <Paper elevation={3} sx={{width:480, height:600, bgcolor:'gray', display:'flex', justifyContent:'center', alignItems:'center'}}>
        {one === true && <ChooseMode handler={handleClick}/>}
        {two === true && <UploadMode/>}
        </Paper>
        
);
}

export default function SimplePaper() {
  return (
    <Container
      sx={{
        display: 'flex',
        //flexWrap: 'wrap',
        justifyContent:'center',
        alignItems:'center',
        height:750,
      }}
    >
     {/* <Paper elevation={3} sx={{width:480, height:600, bgcolor:'gray', display:'flex', justifyContent:'center', alignItems:'center'}}>
    {<CustomGenerate/>}
     </Paper> */}
     <CustomGenerate/>
    </Container>
  );

}

